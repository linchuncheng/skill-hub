{
  "current": "local",
  "local": {
    "type": "kafka",
    "bootstrap_servers": "localhost:9092",
    "sasl_mechanism": "",
    "sasl_plain_username": "",
    "sasl_plain_password": "",
    "security_protocol": "PLAINTEXT"
  },
  "prod": {
    "type": "kafka",
    "bootstrap_servers": "kafka.prod.example.com:9092",
    "sasl_mechanism": "PLAIN",
    "sasl_plain_username": "app",
    "sasl_plain_password": "secret",
    "security_protocol": "SASL_SSL"
  }
}
