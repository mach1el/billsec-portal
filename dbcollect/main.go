package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/lib/pq"       // PostgreSQL driver
	"github.com/robfig/cron/v3" // For scheduling
)

type Config struct {
	DjangoDBConn    string
	DataCentralConn string
}

type ProjectInfo struct {
	Host       string
	Port       int
	SchemaName string
	User       string
	Password   string
}

// Load configuration from environment variables
func loadConfig() (Config, error) {
	config := Config{
		DjangoDBConn:    os.Getenv("DJANGO_DB_CONN"),
		DataCentralConn: os.Getenv("DATA_CENTRAL_CONN"),
	}

	if config.DjangoDBConn == "" || config.DataCentralConn == "" {
		return Config{}, fmt.Errorf("missing required environment variables: DJANGO_DB_CONN or DATA_CENTRAL_CONN")
	}
	return config, nil
}

// Connect to a database with retry logic
func connectDB(connStr string, retries int) (*sql.DB, error) {
	var db *sql.DB
	var err error
	for i := 0; i < retries; i++ {
		db, err = sql.Open("postgres", connStr)
		if err != nil {
			log.Printf("Failed to open DB: %v, retrying...", err)
			time.Sleep(2 * time.Second)
			continue
		}
		if err = db.Ping(); err != nil {
			log.Printf("Failed to ping DB: %v, retrying...", err)
			time.Sleep(2 * time.Second)
			continue
		}
		return db, nil
	}
	return nil, fmt.Errorf("failed to connect after %d retries: %v", retries, err)
}

// Fetch connection details from billing_projectinfo
func getSchemaNames(db *sql.DB) ([]ProjectInfo, error) {
	rows, err := db.Query("SELECT host, port, schema_name, \"user\", password FROM billing_projectinfo")
	if err != nil {
		return nil, fmt.Errorf("query failed: %v", err)
	}
	defer rows.Close()

	var projects []ProjectInfo
	for rows.Next() {
		var p ProjectInfo
		if err := rows.Scan(&p.Host, &p.Port, &p.SchemaName, &p.User, &p.Password); err != nil {
			return nil, err
		}
		projects = append(projects, p)
	}
	return projects, rows.Err()
}

// Check if table exists in data_central
func tableExists(db *sql.DB, schemaName string) (bool, error) {
	query := `
		SELECT EXISTS (
			SELECT 1 
			FROM information_schema.tables 
			WHERE table_schema = 'public' 
			AND table_name = $1
		)`
	var exists bool
	err := db.QueryRow(query, schemaName).Scan(&exists)
	if err != nil {
		return false, fmt.Errorf("failed to check if table %s exists: %v", schemaName, err)
	}
	return exists, nil
}

// Create table in data_central only if it doesn't exist
func createTable(dataCentralDB *sql.DB, schemaName string) error {
	exists, err := tableExists(dataCentralDB, schemaName)
	if err != nil {
		return err
	}
	if exists {
		log.Printf("Table %s already exists in data_central, skipping creation", schemaName)
		return nil
	}

	query := fmt.Sprintf(`
		CREATE TABLE %s (
			id SERIAL PRIMARY KEY NOT NULL,
			method VARCHAR(16) DEFAULT '' NOT NULL,
			from_tag VARCHAR(64) DEFAULT '' NOT NULL,
			to_tag VARCHAR(64) DEFAULT '' NOT NULL,
			callid VARCHAR(64) DEFAULT '' NOT NULL,
			sip_code VARCHAR(3) DEFAULT '' NOT NULL,
			sip_reason VARCHAR(32) DEFAULT '' NOT NULL,
			time TIMESTAMP WITHOUT TIME ZONE NOT NULL,
			duration INTEGER DEFAULT 0 NOT NULL,
			ms_duration INTEGER DEFAULT 0 NOT NULL,
			setuptime INTEGER DEFAULT 0 NOT NULL,
			created TIMESTAMP WITHOUT TIME ZONE DEFAULT NULL,
			src_ip VARCHAR(64) DEFAULT '' NULL,
			dst_ip VARCHAR(64) DEFAULT '' NULL,
			agent VARCHAR(64) DEFAULT '' NULL,
			prefix INTEGER DEFAULT 0 NULL,
			carrier VARCHAR(64) DEFAULT '' NULL
		)`, schemaName)
	_, err = dataCentralDB.Exec(query)
	if err != nil {
		return fmt.Errorf("failed to create table %s: %v", schemaName, err)
	}
	log.Printf("Created table %s in data_central", schemaName)
	return nil
}

// Collect data from acc table in target database and insert into data_central, excluding id
func collectData(targetDB, dataCentralDB *sql.DB, schemaName string) error {
	query := `
		SELECT method, from_tag, to_tag, callid, sip_code, sip_reason, time, 
		  duration, ms_duration, setuptime, created, src_ip, dst_ip, exten, prefix, carrier 
		FROM acc`
	rows, err := targetDB.Query(query)
	if err != nil {
		return fmt.Errorf("failed to query acc table for %s: %v", schemaName, err)
	}
	defer rows.Close()

	insertQuery := fmt.Sprintf(`
		INSERT INTO %s (
			method, from_tag, to_tag, callid, sip_code, sip_reason, time, 
			duration, ms_duration, setuptime, created, src_ip, dst_ip, agent, prefix, carrier
		)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)`, schemaName)

	count := 0
	for rows.Next() {
		var method, fromTag, toTag, callid, sipCode, sipReason string
		var timeVal time.Time
		var duration, msDuration, setuptime int
		var created sql.NullTime
		var srcIP, dstIP, agent sql.NullString
		var prefix sql.NullInt32
		var carrier sql.NullString

		if err := rows.Scan(&method, &fromTag, &toTag, &callid, &sipCode, &sipReason, &timeVal,
			&duration, &msDuration, &setuptime, &created, &srcIP, &dstIP, &agent, &prefix, &carrier); err != nil {
			return fmt.Errorf("scan failed for %s: %v", schemaName, err)
		}

		_, err := dataCentralDB.Exec(insertQuery, method, fromTag, toTag, callid, sipCode, sipReason, timeVal,
			duration, msDuration, setuptime, created, srcIP, dstIP, agent, prefix, carrier)
		if err != nil {
			return fmt.Errorf("insert failed for %s: %v", schemaName, err)
		}
		count++
	}
	log.Printf("Inserted %d rows into %s", count, schemaName)
	return nil
}

// Main collection logic
func runCollection(config Config) error {
	log.Printf("DJANGO_DB_CONN: %s", config.DjangoDBConn)
	log.Printf("DATA_CENTRAL_CONN: %s", config.DataCentralConn)

	// Connect to Django DB to get metadata
	djangoDB, err := connectDB(config.DjangoDBConn, 3)
	if err != nil {
		return fmt.Errorf("django_db connection failed: %v", err)
	}
	defer djangoDB.Close()

	// Connect to data_central for storage
	dataCentralDB, err := connectDB(config.DataCentralConn, 3)
	if err != nil {
		return fmt.Errorf("data_central connection failed: %v", err)
	}
	defer dataCentralDB.Close()

	// Fetch target database connection details
	projects, err := getSchemaNames(djangoDB)
	if err != nil {
		return fmt.Errorf("failed to fetch schema names: %v", err)
	}

	if len(projects) == 0 {
		log.Println("No schemas found in billing_projectinfo, skipping table creation and data insertion")
		return nil
	}

	for _, project := range projects {
		// Construct connection string for target database
		targetConnStr := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
			project.Host, project.Port, project.User, project.Password, project.SchemaName)

		// Connect to the target database
		targetDB, err := connectDB(targetConnStr, 3)
		if err != nil {
			log.Printf("Failed to connect to target DB %s: %v", project.SchemaName, err)
			continue
		}
		defer targetDB.Close()

		// Create table in data_central if it doesn’t exist
		if err := createTable(dataCentralDB, project.SchemaName); err != nil {
			log.Printf("Error creating table %s: %v", project.SchemaName, err)
			continue
		}

		// Collect data from target DB and insert into data_central
		if err := collectData(targetDB, dataCentralDB, project.SchemaName); err != nil {
			log.Printf("Error collecting data for %s: %v", project.SchemaName, err)
			continue
		}
	}
	return nil
}

func main() {
	config, err := loadConfig()
	if err != nil {
		log.Fatalf("Config load failed: %v", err)
	}

	// Run once at startup
	log.Println("Starting dbcollect service...")
	if err := runCollection(config); err != nil {
		log.Printf("Initial run failed: %v", err)
	}

	// Schedule daily run at 23:00
	c := cron.New()
	_, err = c.AddFunc("00 23 * * *", func() {
		log.Println("Running scheduled data collection...")
		if err := runCollection(config); err != nil {
			log.Printf("Scheduled run failed: %v", err)
		} else {
			log.Println("Scheduled run completed successfully")
		}
	})
	if err != nil {
		log.Fatalf("Failed to schedule cron job: %v", err)
	}
	c.Start()

	// Keep the service running
	select {}
}
