package com.example.demo;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/customers")
public class CustomerSearchController {

    @GetMapping("/{customerID}")
    public Customer searchCustomer(@PathVariable String customerID) {
        //Implementation to fetch Customer based on customerID from database.  This would typically involve a service layer call.
        //Placeholder return for demonstration purposes.  Replace with actual database interaction.
        return new Customer(customerID, "John Doe", "john.doe@example.com");
    }


    static class Customer {
        String customerID;
        String name;
        String email;

        public Customer(String customerID, String name, String email) {
            this.customerID = customerID;
            this.name = name;
            this.email = email;
        }

        //Getters and setters (omitted for brevity)
    }
}