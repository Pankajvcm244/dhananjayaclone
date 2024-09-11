def prepare_email_body(dr_doc):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Donation Receipt</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}

        .email-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #fff;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}

        h1 {{
            color: #333;
        }}

        p {{
            color: #555;
        }}

        .signature {{
            margin-top: 20px;
            font-style: italic;
            color: #888;
        }}
    </style>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
    <div class="email-container" style="max-width: 600px; margin: 0 auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
        <h1 style="color: #333;">Hare Krishna!</h1>

        <p style="color: #555;">We deeply appreciate your recent contribution to {dr_doc.company}. Attached is your donation receipt for your records. 🙏</p>

        <p style="color: #555;">
            <strong>Receipt Number:</strong> {dr_doc.name}<br>
            <strong>Donation Amount:</strong> {dr_doc.amount}
        </p>

        <p style="color: #555;">Your support makes a significant impact. Thank you for helping us make a difference. 🌈</p>

        <p style="color: #555;">Best Regards, <br>
        Donor Care Team</p>

        <div class="signature" style="margin-top: 20px; font-style: italic; color: #888;">🌟</div>
    </div>
</body>
</html>"""
