FROM python:2.7

RUN curl -o /bin/borg -L https://github.com/borgbackup/borg/releases/download/1.1.0rc3/borg-linux64 && \
    chown root:root /bin/borg && \
    chmod 755 /bin/borg
