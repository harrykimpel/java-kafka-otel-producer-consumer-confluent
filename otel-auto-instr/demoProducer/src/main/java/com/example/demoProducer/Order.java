package com.example.demoProducer;

import lombok.Data;

import java.util.Date;

@Data
public class Order {

    private String customerId;

    public String getCustomerId() {
        return customerId;
    }

    private String orderId;

    public String getOrderId() {
        return orderId;
    }

    private Date dateOfCreation;

    private String input;

    public String getInput() {
        return input;
    }

    private String content;

    public String getContent() {
        return content;
    }
}
