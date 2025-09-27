package com.example.demo;

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/session")
public class SessionManagementController {

    private boolean sessionActive = false;
    private String currentUsername = "";


    @PostMapping("/start")
    public Boolean startSession(@RequestParam String username) {
        if (!sessionActive) {
            sessionActive = true;
            currentUsername = username;
            return true;
        }
        return false;
    }

    @PostMapping("/end")
    public void endSession() {
        sessionActive = false;
        currentUsername = "";
    }
}