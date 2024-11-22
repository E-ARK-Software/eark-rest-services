# Now build a Java JRE for the Alpine application image
# https://github.com/docker-library/docs/blob/master/eclipse-temurin/README.md#creating-a-jre-using-jlink
FROM eclipse-temurin:17-jdk-alpine AS jre-builder

# Create a custom Java runtime
# ,java.logging,java.xml,java.management,java.desktop,jdk.zipfs \
RUN "$JAVA_HOME/bin/jlink" \
         --add-modules java.base,java.xml,java.naming,java.desktop,jdk.zipfs \
         --strip-debug \
         --no-man-pages \
         --no-header-files \
         --compress=2 \
         --output /javaruntime

FROM python:3.11-alpine

# We need git to install the requirements
RUN apk add --no-cache git

# Set up dumb-init for process safety: https://github.com/Yelp/dumb-init
ADD --link https://github.com/Yelp/dumb-init/releases/download/v1.2.5/dumb-init_1.2.5_x86_64 /usr/local/bin/dumb-init 
RUN chmod +x /usr/local/bin/dumb-init

# Set for additional arguments passed to the java run command, no default
ARG JAVA_OPTS
ENV JAVA_OPTS=$JAVA_OPTS

# Copy the JRE from the previous stage
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH "${JAVA_HOME}/bin:${PATH}"
COPY --from=jre-builder /javaruntime $JAVA_HOME

WORKDIR /opt/eark-rest

# Since this is a running network service we'll create an unprivileged account
# which will be used to perform the rest of the work and run the actual service:
RUN addgroup -S eark-rest && adduser --system -D --home /opt/eark-rest -G eark-rest eark-rest
RUN mkdir --parents /opt/eark-rest && chown -R eark-rest:eark-rest /opt/eark-rest

# Get the commons-ip jar
ADD --link https://github.com/keeps/commons-ip/releases/download/2.8.1/commons-ip2-cli-2.8.1.jar /opt/eark-rest/commons-ip/commons-ip2-cli-2.8.1.jar
RUN chown -R eark-rest:eark-rest /opt/eark-rest/commons-ip

# Work as the unprivileged user now
USER eark-rest

COPY ./requirements.txt /opt/eark-rest/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /opt/eark-rest/requirements.txt

COPY .env /opt/eark-rest/.env
COPY ./static /opt/eark-rest/static
COPY ./templates /opt/eark-rest/templates
COPY ./app /opt/eark-rest/app

ENTRYPOINT [ "dumb-init", "--" ]
CMD ["/opt/eark-rest/.local/bin/fastapi", "run", "/opt/eark-rest/app/main.py"]