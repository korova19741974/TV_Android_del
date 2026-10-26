package com.gathin.tvhome;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

import java.io.IOException;

/** Arms the next-key learner when the trusted Windows setup tool calls it over ADB. */
public final class KeyLearningReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        if (!KeyLearning.ACTION.equals(intent.getAction())) return;
        try {
            setResultCode(0);
            setResultData(KeyLearning.arm(context));
        } catch (IOException error) {
            setResultCode(1);
            setResultData(error.getMessage());
        }
    }
}
