package com.example.demoConsumer;

import com.example.demoProducer.Order;
import com.example.demoConsumer.User;
import com.example.demoConsumer.UserProducer;

import org.springframework.beans.factory.annotation.Autowired;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URI;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.messaging.handler.annotation.Headers;
import org.springframework.kafka.listener.adapter.ConsumerRecordMetadata;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;

import java.util.Map;
import java.util.concurrent.ExecutionException;
import com.newrelic.api.agent.NewRelic;
import com.newrelic.api.agent.Trace;
import com.newrelic.api.agent.HeaderType;
import com.newrelic.api.agent.ConcurrentHashMapHeaders;
import com.newrelic.api.agent.TransportType;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.apache.commons.codec.binary.Base64;

@Service("orderConsumerNotificationService")
public class CreateOrderConsumer {

    private static final Logger log = LoggerFactory.getLogger(CreateOrderConsumer.class);

    private final UserProducer userProducer;

    @Autowired
    CreateOrderConsumer(UserProducer userProducer) {
        this.userProducer = userProducer;
    }

    @Trace(dispatcher = true)
    @KafkaListener(topics = "${spring.kafka.order.topic.create-order}", containerFactory = "containerFactoryNotificationService")
    public void createOrderListener(@Payload Order order, Acknowledgment ack, @Headers Map<String, Object> headers,
            ConsumerRecordMetadata meta) {
        // create a distributed trace headers map
        com.newrelic.api.agent.Headers dtHeaders = ConcurrentHashMapHeaders.build(HeaderType.MESSAGE);

        log.info("Kafka meta received: " + meta.toString());

        // Iterate through each record header and insert the trace headers into the
        // dtHeaders map
        //
        headers.forEach((key, value) -> {
            // String headerValue = value.toString();
            // String headerValue = new String(value, StandardCharsets.UTF_8);
            // byte ptext[] = value.getBytes();
            String headerValue = value.toString();
            byte[] data = null;

            try {
                data = new ObjectMapper().writeValueAsBytes(value);
                headerValue = new String(data, "UTF-8");
            } catch (Exception e) {
                log.error("Error converting header value to string: " + e.getMessage());
            }

            log.info("Kafka header key: " + key + " value: " + headerValue);

            // using the newrelic key
            if (key.equals("newrelic")) {
                log.info("New Relic header added");
                Base64 base64 = new Base64();
                String decodedString = new String(base64.decode(data));
                log.info("Kafka header key decoded: " + key + " value: " + decodedString);
                dtHeaders.addHeader("newrelic", decodedString);
            }

            // or using the W3C keys
            if (key.equals("traceparent")) {
                dtHeaders.addHeader("traceparent", headerValue);
            }

            if (key.equals("tracestate")) {
                dtHeaders.addHeader("tracestate", headerValue);
            }
        });

        // Accept distributed tracing headers to link this request to the originating
        // request
        NewRelic.getAgent().getTransaction().acceptDistributedTraceHeaders(TransportType.Kafka, dtHeaders);

        log.info("Notification service received order {} ", order);
        ack.acknowledge();

        if (order.getContent().indexOf("London") != -1)

        {
            log.error("Error in order content: " + order.getContent());
        }

        CallDemoService1();

        CallDemoService2();

        SecureRandom secureRandom = new SecureRandom();
        int secondsToSleep = 3 + secureRandom.nextInt(5);
        ;

        ExecuteLongrunningTask(secondsToSleep);

        int randomWithSecureRandom = secureRandom.nextInt(10);
        if (order.getCustomerId().equals("0")) {
            randomWithSecureRandom = 0;
        }
        log.info("randomWithSecureRandom: " + randomWithSecureRandom);
        User user = GetUser(randomWithSecureRandom);

        try {
            sendUserEvent(user);
        } catch (ExecutionException e) {
            throw new RuntimeException(e);
        } catch (InterruptedException e) {
        }
    }

    private boolean sendUserEvent(User user) throws ExecutionException, InterruptedException {

        userProducer.sendUserEvent(user);

        return true;
    }

    private void ExecuteLongrunningTask(Integer secondsToSleep) {
        try {
            Thread.sleep(secondsToSleep * 1000);
            log.info("Executed some long running task that took " + secondsToSleep + " seconds to run.");
        } catch (Exception ex) {

        }
    }

    private User GetUser(Integer randomUser) {
        String uri = "https://jsonplaceholder.typicode.com/users/" + randomUser;
        RestTemplate restTemplate = new RestTemplate();

        User user = restTemplate.getForObject(uri, User.class);
        int userId = user.getId();
        log.info("User: " + user);
        log.info("User id: " + userId);

        return user;
    }

    private void CallDemoService1() {
        try {
            String uri = "http://localhost:8082";
            String userAgent = "java.net.HttpURLConnection";

            URL obj = URI.create(uri).toURL();
            HttpURLConnection con = (HttpURLConnection) obj.openConnection();
            con.setRequestMethod("GET");
            con.setRequestProperty("User-Agent", userAgent);
            int responseCode = con.getResponseCode();
            System.out.println("GET Response Code :: " + responseCode);
            if (responseCode == HttpURLConnection.HTTP_OK) { // success
                BufferedReader in = new BufferedReader(new InputStreamReader(con.getInputStream()));
                String inputLine;
                StringBuffer response = new StringBuffer();

                while ((inputLine = in.readLine()) != null) {
                    response.append(inputLine);
                }
                in.close();

                // print result
                log.info("Demo Service response: " + response.toString());
            } else {
                log.info("GET request did not work.");
            }
        } catch (Exception ex) {

        }
    }

    private void CallDemoService2() {
        String uri = "http://localhost:8082";
        RestTemplate restTemplate = new RestTemplate();
        String resp = restTemplate.getForObject(uri, String.class);

        log.info("Demo Service response: " + resp);
    }
}
