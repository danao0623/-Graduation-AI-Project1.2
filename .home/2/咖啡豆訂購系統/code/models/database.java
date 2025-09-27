package com.example.demo;

import lombok.Data;
import org.springframework.stereotype.Repository;

import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Repository
@Data
public class Database {
    private List<Order> orders = new ArrayList<>();

    public Order getOrder(String orderID) {
        return orders.stream().filter(order -> order.getOrderID().equals(orderID)).findFirst().orElse(null);
    }

    public List<Order> getOrder(String customerID) {
        return orders.stream().filter(order -> order.getCustomerID().equals(customerID)).collect(Collectors.toList());
    }


    @Data
    public static class Order {
        private String orderID;
        private String customerID;
        //other attributes
    }
}