#!/bin/bash
# 设置mysql的登录用户名和密码(根据实际情况填写)
mysql_user="root"
mysql_password="123456"
mysql_host="192.168.3.200"
mysql_port="3306"
mysql_charset="utf8mb4"
mysql_dbname="fastapi"
mysql_docker="mysql-test"
 
# 备份文件存放地址 docker  /code/sql
backup_location=/home/infra/simulation/trunkverse_service/sql
 
# 是否删除过期数据
expire_backup_delete="ON"
expire_days=7
backup_time=`date +%Y%m%d%H%M`
backup_dir=$backup_location
welcome_msg="Welcome to use MySQL backup tools!"

# 备份指定数据库中数据(此处假设数据库是mysql_backup_test)
docker exec -it $mysql_docker mysqldump -h$mysql_host -P$mysql_port -u$mysql_user -p$mysql_password -B test1 > $backup_dir/$mysql_dbname-$backup_time.sql
echo "备份完成！"

# 删除过期数据
if [ "$expire_backup_delete" == "ON" -a "$backup_location" != "" ]; then
        `find $backup_location/ -type f -mtime +$expire_days | xargs rm -rf`
        echo "过期数据删除完成!"
fi
