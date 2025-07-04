export JAVA_TOOL_OPTIONS="-javaagent:../../newrelic.jar"
export OTEL_TRACES_EXPORTER=otlp
export OTEL_METRICS_EXPORTER=otlp
export OTEL_LOGS_EXPORTER=otlp
# US region
export OTEL_EXPORTER_OTLP_ENDPOINT='https://otlp.nr-data.net'
# EU region
#export OTEL_EXPORTER_OTLP_ENDPOINT='https://otlp.eu01.nr-data.net'
export OTEL_EXPORTER_OTLP_HEADERS="api-key=MY_NEW_RELIC_LICENSE_KEY"
export OTEL_SERVICE_NAME="kafka-java-service"

export NEW_RELIC_APP_NAME="kafka-java-service"
export NEW_RELIC_LICENSE_KEY="MY_NEW_RELIC_LICENSE_KEY"

./mvnw spring-boot:run