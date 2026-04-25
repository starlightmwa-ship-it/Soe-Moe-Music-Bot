FROM golang:1.21-alpine AS builder

WORKDIR /app

# Install dependencies
RUN apk add --no-cache git ca-certificates

# Copy go mod files
COPY go.mod go.sum ./
RUN go mod download

# Copy source and build
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o tgmusicbot .

# Final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates ffmpeg

WORKDIR /root/

# Copy binary from builder
COPY --from=builder /app/tgmusicbot .
COPY --from=builder /app/.env .env 2>/dev/null || true

# Expose port (not strictly needed for bot, but for Render)
EXPOSE 8080

CMD ["./tgmusicbot"]
