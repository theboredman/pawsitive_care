class RecordObserver:
    def notify(self, record):
        # You could send an email, log activity, or send notification.
        print(f"✅ New medical record created for {record.pet.name}")
