import smtplib
server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login("sathya.s.ihub@snsgroups.com", "ogmh fkzd arhr fnzp")
print("✅ SMTP login successful")
server.quit()
