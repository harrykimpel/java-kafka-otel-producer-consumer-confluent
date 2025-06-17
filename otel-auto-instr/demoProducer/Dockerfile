FROM openjdk:21-jdk-slim
COPY opentelemetry-javaagent.jar opentelemetry-javaagent.jar
COPY mvnw mvnw
COPY run.sh run.sh
COPY target/demoProducer-0.0.1-SNAPSHOT.jar demoProducer.jar
ENV NEW_RELIC_LICENSE_KEY=${NEW_RELIC_LICENSE_KEY}
ENTRYPOINT ["./run.sh"]