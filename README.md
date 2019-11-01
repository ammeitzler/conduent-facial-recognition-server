## Installation :
1. docker-compose build
2. docker volume prune
3. docker system prune	
4. docker-compose up

## Endpoints :
1. /analyzeImage/ POST (returns uuid)
2. /entities/uuid POST (returns uuid of match)
3. /entities/uuid GET (returns stylized image)
4. /entities/uuid DELETE (deletes entry)
5. /media/<uuid>.jpeg (retrieves jpeg image)
6. /media/vect-<uuid>.mesh (retrieves ivans binary image)