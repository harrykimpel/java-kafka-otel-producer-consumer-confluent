package com.example.demoConsumer;

import com.example.demoProducer.Order;

import io.opentelemetry.instrumentation.kafkaclients.v2_6.TracingConsumerInterceptor;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.common.serialization.StringDeserializer;
import org.apache.kafka.common.serialization.StringSerializer;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.annotation.EnableKafka;
import org.springframework.kafka.config.ConcurrentKafkaListenerContainerFactory;
import org.springframework.kafka.core.ConsumerFactory;
import org.springframework.kafka.core.DefaultKafkaConsumerFactory;
import org.springframework.kafka.listener.ContainerProperties;
import org.springframework.kafka.support.serializer.JsonDeserializer;
import org.springframework.kafka.support.serializer.JsonSerializer;

import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@EnableKafka
@Configuration("consumerConfigNotificationService")
public class CreateOrderConsumerConfig {

    @Value("${spring.kafka.bootstrap-servers}")
    private String bootstrapServers;

    @Value("${spring.kafka.order.consumer.group-id.notification}")
    private String groupId;

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

    @Bean("orderConsumerFactoryNotificationService")
    public ConsumerFactory<String, Order> createOrderConsumerFactory() {
        Map<String, Object> props = new HashMap<>();
        props.put(
                ConsumerConfig.INTERCEPTOR_CLASSES_CONFIG,
                TracingConsumerInterceptor.class.getName());
        props.put(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, bootstrapServers);
        props.put("sasl.jaas.config", saslJaaSConfig);
        props.put("security.protocol", securityProtocol);
        props.put("sasl.mechanism", saslMechanism);
        // props.put("client.dns.lookup", clientDnsLookup);
        props.put("acks", acks);
        props.put("group.id.config", "java-group-1");
        props.put("application.id", "orders");
        props.put("auto.offset.reset.config", "earliest");
        props.put(ConsumerConfig.GROUP_ID_CONFIG, groupId);
        props.put(ConsumerConfig.CLIENT_ID_CONFIG, UUID.randomUUID().toString());
        props.put(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringSerializer.class);
        props.put(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, JsonSerializer.class);
        props.put(ConsumerConfig.ENABLE_AUTO_COMMIT_CONFIG, false);

        return new DefaultKafkaConsumerFactory<>(props, new StringDeserializer(),
                new JsonDeserializer<>(Order.class));
    }

    @Bean("containerFactoryNotificationService")
    public ConcurrentKafkaListenerContainerFactory<String, Order> createOrderKafkaListenerContainerFactory() {
        ConcurrentKafkaListenerContainerFactory<String, Order> factory = new ConcurrentKafkaListenerContainerFactory<>();
        factory.setConsumerFactory(createOrderConsumerFactory());
        factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL_IMMEDIATE);
        return factory;
    }
}
