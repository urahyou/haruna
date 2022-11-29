import smtplib
from email.mime.text import MIMEText
from email.header import Header

# 创建 SMTP 对象
smtp = smtplib.SMTP()
# 连接（connect）指定服务器
smtp.connect("smtp.qq.com", port=587)
# 登录，需要：登录邮箱和授权码
smtp.login(user="2726717369@qq.com", password="gljhcndoqpyrdgcc")

# 构造MIMEText对象，参数为：正文，MIME的subtype，编码方式
message = MIMEText('你好，我是urahyou', 'plain', 'utf-8')
message['From'] = Header("hello", 'utf-8')  # 发件人的昵称
message['To'] = Header("jack", 'utf-8')  # 收件人的昵称
message['Subject'] = Header('Python SMTP 邮件测试', 'utf-8')  # 定义主题内容
print(message)

smtp.sendmail(from_addr="2726717369@qq.com", to_addrs="17607582272@163.com", msg=message.as_string())
