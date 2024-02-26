from watcher import connect_to_db, auto_check


conn, cursor = connect_to_db()
auto_check(conn,cursor)
if conn.is_connected() == True:
   conn.close()