FROM mcr.microsoft.com/azure-cli

ARG azsubid
ENV AZURE_SUBSCRIPTION_ID $azsubid

WORKDIR /root
COPY . .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

#CMD ["python", "./azure-api.py"]
CMD ["/bin/bash"]

