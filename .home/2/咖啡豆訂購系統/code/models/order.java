package com.example.demo;

import lombok.Data;
import javax.persistence.*;

@Entity
@Data
public class Order {
    @Id
    private String orderID;
    private String customerID;
    private String orderStatus;
    private String orderDetails;

    public void updateStatus(String status) {
        this.orderStatus = status;
    }

    public void updateDetails(String details) {
        this.orderDetails = details;
    }
}

package com.example.demo;

import lombok.Data;
import javax.persistence.*;

@Entity
@Data
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String orderID;
    private String customerID;
    private String orderStatus;


    public String getOrderStatus() {
        return orderStatus;
    }
}