package com.example.demo;

import lombok.Data;
import javax.persistence.*;
import java.util.List;

@Entity
@Data
public class Customer {

    @Id
    private String customerID;

    private String customerInfo;

    @OneToMany(mappedBy = "customer", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<Inquiry> inquiries;
}

package com.example.demo;

import lombok.Data;
import javax.persistence.*;

@Entity
@Data
public class Inquiry {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long inquiryID;

    private String inquiryContent;

    @ManyToOne
    @JoinColumn(name = "customerID")
    private Customer customer;
}

package com.example.demo;

import lombok.Data;
import javax.persistence.*;

@Entity
@Data
public class Customer {

    @Id
    private String customerID;
    private String customerName;
    private String customerEmail;
    private String customerAddress;
}