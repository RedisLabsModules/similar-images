
cat EfficientNetB0.pb | redis-cli -x AI.MODELSET efficient TF CPU INPUTS x OUTPUTS Identity BLOB
