# Stage 1: Build the Go binary
FROM golang:1.22 AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o dbcollect

FROM alpine:latest

WORKDIR /app

RUN apk --no-cache add ca-certificates tzdata

COPY --from=builder /app/dbcollect .

COPY .env .env

ENV TZ=UTC

CMD ["./dbcollect"]