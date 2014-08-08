from app import db, models

fedex = models.Carrier(id = 402645, name = 'fedex', dispute_emails = 'kim.robertson@fedex.com; quickresponse7@fedex.com; fedexcollections@fedex.com: fedex.com/us/account/invhome/other/eremit.html' , payment_release_emails = 'kim.robertson@fedex.com; useft@fedex.com; eremit@fedex.com')
ups_dom = models.Carrier(id = 402919, name = 'ups_dom', dispute_emails = 'mxarmstrong@ups.com; ajoly@ups.com', payment_release_emails = 'achdetail@ups.com; mxarmstrong@ups.com; ajoly@ups.com')
ups_imp = models.Carrier(id = 402623, name = 'ups_imp', dispute_emails = 'preferred.us@ups.com; srbrown@ups.com; ajoly@ups.com', payment_release_emails = 'paymentremit@ups.com; srbrown@ups.com; ajoly@ups.com; kminal@ups.com; WST3XYF@upsstore.com')
schenker = models.Carrier(id = 804244, name = 'schenker', dispute_emails = 'kathleen.clarke@dbschenker.com', payment_release_emails = 'kathleen.clarke@dbschenker.com')
dhl = models.Carrier(id = 402604, name = 'dhl', dispute_emails = 'henry.leon@dhl.com', payment_release_emails = 'henry.leon@dhl.com')
mnx = models.Carrier(id = 807354, name = 'mnx', dispute_emails = 'accounts.receivable@mnx.com', payment_release_emails = 'accounts.receivable@mnx.com')
sterling = models.Carrier(id = 402885, name = 'sterling', dispute_emails = 'diane_angus@qintl.com', payment_release_emails = 'diane_angus@qintl.com')
gzuz = models.Carrier(id = 805968, name = 'gzuz', dispute_emails = '', payment_release_emails = '')