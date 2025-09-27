package com.example.demo;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ReplyController {

    @PostMapping("/checkReplyContent")
    public Boolean checkReplyContent(@RequestBody String replyContent) {
        //  Implementation to check reply content.  Replace with your actual logic.
        return replyContent != null && !replyContent.isEmpty();
    }
}