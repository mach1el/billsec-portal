# Stage 1: Build the Go binary
FROM golang:1.24 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o dbcollect

FROM alpine:latest

ENV DJANGO_DB_CONN=$DJANGO_DB_CONN \
  DATA_CENTRAL_CONN=$DATA_CENTRAL_CONN \
  DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY

WORKDIR /app

RUN apk --no-cache add ca-certificates tzdata

COPY --from=builder /app/dbcollect .

CMD ["./dbcollect"]