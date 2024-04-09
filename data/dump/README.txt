1. Download the database dump
2. Make sure that the name of the database dump (postgres.dump_2024_04_07.tar) matches the variable DB_NAME in restore.sh
3. Install docker and start docker daemon 
4. run: (sudo) bash restore.sh 
5. run: (sudo) docker compose up 
6. open DBeaver and connect to database using config in restore.sh comments 
7. run the extract_answers.sql file in DBeaver to extract raw.csv 
8. run extract_entities.sql file in DBeaver to extract entry_tags.csv 
9. run extract_region.sql file in DBeaver to extract region_tags.csv 
10. run 

Additionally (done to check new pipeline): 
10a. repeat steps 2, 4, 5, 6, 7 with the legacy database dump (postgres.dump.tar) to extract raw_legacy.csv 
10b. verify that raw.csv corresponds (or that differences reflect correct changes) in verify_entries.py and verify_questions.py 

