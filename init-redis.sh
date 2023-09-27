#!/bin/bash
echo "Waiting for redis setup..."
sleep 10
# shellcheck disable=SC2016
redis-cli -h redis SET user:404bdab1-3dd5-4173-9713-43ec7858b0b5 '{
    "id": "404bdab1-3dd5-4173-9713-43ec7858b0b5",
    "first_name": "Admin",
    "last_name": "admin",
    "gender": "male",
    "roles": [
        "user",
        "admin",
        "manager"
    ],
    "is_activated": true,
    "activated_at": 1694973156028615700,
    "updated_at": 1694973923188866800,
    "in_charge": [],
    "managed_by": null,
    "entity_type": "User",
    "hashed_password": "$2b$12$OC7efOhEtTh/oltt0vRW5Oor.jlTO9AmWY19GP/qAhtKhCQS4yltK"
}'
echo "Redis set up!"