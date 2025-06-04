package com.example.demoProducer;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.core.DefaultKafkaProducerFactory;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.core.ProducerFactory;
import org.springframework.kafka.support.serializer.JsonSerializer;

import java.util.HashMap;
import java.util.Map;

//import io.opentelemetry.instrumentation.kafkaclients.v2_6.TracingProducerInterceptor;

@Configuration
public class CreateOrderProducerConfig {

    @Value("${spring.kafka.bootstrap-servers}")
    private String bootstrapServers;

    @Value("${spring.kafka.properties.sasl.jaas.config}")
    private String saslJaaSConfig;

    @Value("${spring.kafka.properties.security.protocol}")
    private String securityProtocol;

    @Value("${spring.kafka.properties.sasl.mechanism}")
    private String saslMechanism;

    // @Value("${client.dns.lookup}")
    // private String clientDnsLookup;

    @Value("${acks}")
    private String acks;

    @Bean
    public <K, V> ProducerFactory<K, V> createOrderProducerFactory() {
        Map<String, Object> config = new HashMap<>();
        // config.put(
        // org.apache.kafka.clients.producer.ProducerConfig.INTERCEPTOR_CLASSES_CONFIG,
        // TracingProducerInterceptor.class.getName());
        config.put(org.apache.kafka.clients.producer.ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        config.put("sasl.jaas.config", saslJaaSConfig);
        config.put("security.protocol", securityProtocol);
        config.put("sasl.mechanism", saslMechanism);
        // config.put("client.dns.looku", clientDnsLookup);
        config.put("acks", acks);
        config.put("group.id.config", "ccloud-springboot-client-a7cdcb35-30ae-4a9d-bf60-bcf008a0f662");
        config.put("application.id", "orders");
        config.put(org.apache.kafka.clients.producer.ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        config.put(org.apache.kafka.clients.producer.ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
                JsonSerializer.class);

        return new DefaultKafkaProducerFactory(config);
    }

    @Bean
    public <K, V> KafkaTemplate<K, V> createOrderKafkaTemplate() {
        return new KafkaTemplate<>(createOrderProducerFactory());
    }
}
