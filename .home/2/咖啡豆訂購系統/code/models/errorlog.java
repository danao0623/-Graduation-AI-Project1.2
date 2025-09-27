package com.example.demo;

import lombok.Data;
import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Data
public class ErrorLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private LocalDateTime errorTime;
    private String errorMessage;
    private String orderNumber;
}

package com.example.demo;

import lombok.Data;
import javax.persistence.*;
import java.util.Date;

@Entity
@Data
public class ErrorLog {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Temporal(TemporalType.TIMESTAMP)
    private Date timestamp;

    private String message;

    public void logError(String message) {
        this.timestamp = new Date();
        this.message = message;
    }
}