from electionsproject.settings_general import S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET
import tinys3


## set up and call the s3 connection using tinyS3
def s3_connection():
    
    connection = tinys3.Connection(
        S3_ACCESS_KEY, 
        S3_SECRET_KEY, 
        default_bucket=S3_BUCKET', 
        tls=True
    )

    return connection
