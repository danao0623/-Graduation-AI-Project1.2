package com.example.demo;

import lombok.Data;
import javax.persistence.*;

@Entity
@Data
public class User {
    @Id
    private String userID;
    private String username;
    private String role;

    public String getUserRole() {
        return role;
    }
}