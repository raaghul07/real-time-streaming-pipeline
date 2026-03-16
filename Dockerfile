# Base image: ubuntu:22.04
FROM ubuntu:22.04

# ARGs
# https://docs.docker.com/engine/reference/builder/#understand-how-arg-and-from-interact
ARG TARGETPLATFORM=linux/amd64,linux/arm64
ARG DEBIAN_FRONTEND=noninteractive
ARG GITHUB_TOKEN

# neo4j 5.5.0 installation and some cleanup
RUN apt-get update && \
    apt-get install -y wget gnupg git software-properties-common && \
    wget -O - https://debian.neo4j.com/neotechnology.gpg.key | apt-key add - && \
    echo 'deb https://debian.neo4j.com stable latest' > /etc/apt/sources.list.d/neo4j.list && \
    add-apt-repository universe && \
    apt-get update && \
    apt-get install -y nano unzip neo4j python3-pip && \
    apt-get autoremove -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Set password (so it matches project requirement)
ENV NEO4J_AUTH=neo4j/project1phase1


# Install Python libraries
RUN pip3 install --upgrade pip && \
    pip3 install pandas pyarrow neo4j requests

# Download and install GDS plugin manually (version 2.15.0)
RUN wget https://graphdatascience.ninja/neo4j-graph-data-science-2.15.0.zip -O gds.zip && \
    unzip gds.zip -d /var/lib/neo4j/plugins/ && \
    rm gds.zip

# Set working directory
WORKDIR /cse511

# Download the March 2022 Yellow Cab dataset
RUN wget https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2022-03.parquet -O yellow_tripdata_2022-03.parquet

# Clone private GitHub repo and copy python into working directory
RUN git clone https://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@github.com/SP-2025-CSE511-Data-Processing-at-Scale/Project-1-rkanna18.git /tmp/repo && \
    ls -l /tmp/repo && \
    cp /tmp/repo/data_loader.py /cse511/data_loader.py && \
    cp /tmp/repo/interface.py /cse511/interface.py && \
    cp /tmp/repo/tester.py /cse511/tester.py && \
    rm -rf /tmp/repo

# Update neo4j.conf to enable GDS and remote access
RUN echo "dbms.security.procedures.unrestricted=gds.*" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.security.procedures.allowlist=gds.*" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.default_listen_address=0.0.0.0" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.default_advertised_address=localhost" >> /etc/neo4j/neo4j.conf && \
    echo "dbms.security.auth_enabled=true" >> /etc/neo4j/neo4j.conf
RUN neo4j-admin dbms set-initial-password project1phase1


# Run the data loader script
RUN chmod +x /cse511/data_loader.py && \
    neo4j start && \
    python3 data_loader.py && \
    neo4j stop

# Expose neo4j ports
EXPOSE 7474 7687

# Start neo4j service and show the logs on container run
CMD ["/bin/bash", "-c", "neo4j start && tail -f /dev/null"]    



