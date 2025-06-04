for i in {1..5}; do \                                                ✔  12s   07:51:01 PM  
    for j in {1..10}; do \
        curl -X POST -H 'Content-Type: application/json' \
            -d '{ "customerId":  '$i', "orderId": '$j', "dateOfCreation": "2025-05-28", "content": "I love coffee in Ljubljana"}' \
            http://localhost:8080/orders 
        echo "Order $j for customer $i created"
        # Adding a short sleep to avoid overwhelming the server
        sleep 0.1
    ; done
    sleep 0.2
; done