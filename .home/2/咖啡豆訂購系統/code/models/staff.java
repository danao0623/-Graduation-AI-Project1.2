package com.example.demo;

import lombok.Data;
import javax.persistence.*;

@Entity
@Data
public class Staff {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String staffID;
    private String username;
    private String password;
}