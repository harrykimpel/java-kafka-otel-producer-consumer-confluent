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
import java.security.SecureRandom;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;

import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.support.Acknowledgment;
import org.springframework.messaging.handler.annotation.Payload;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.kafka.support.SendResult;
import java.util.concurrent.ExecutionException;

@Service("orderConsumerNotificationService")
public class CreateOrderConsumer {

    private static final Logger log = LoggerFactory.getLogger(CreateOrderConsumer.class);

    private final UserProducer userProducer;

    @Autowired
    CreateOrderConsumer(UserProducer userProducer) {
        this.userProducer = userProducer;
    }

    @KafkaListener(topics = "${spring.kafka.order.topic.create-order}", containerFactory = "containerFactoryNotificationService")
    public void createOrderListener(@Payload Order order, Acknowledgment ack) {
        log.info("Notification service received order {} ", order);
        ack.acknowledge();

        if (order.getContent().indexOf("London") != -1) {
            log.error("Error in order content: " + order.getContent());
        }

        CallDemoService1();

        CallDemoService2();

        SecureRandom secureRandom = new SecureRandom();

        int randomTimeToSleep = secureRandom.nextInt(5);
        Integer secondsToSleep = 3 + randomTimeToSleep;
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
