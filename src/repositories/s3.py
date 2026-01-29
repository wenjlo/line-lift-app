import boto3
from botocore.exceptions import NoCredentialsError, ClientError


def upload_to_r2(local_file_path, bucket_name, object_name, account_id, access_key, secret_key):
    """
    將本地檔案上傳至 Cloudflare R2

    :param local_file_path: 本地檔案路徑
    :param bucket_name: R2 儲存桶名稱
    :param object_name: 上傳後的檔案名稱 (路徑)
    :param account_id: Cloudflare 帳戶 ID
    :param access_key: R2 Access Key ID
    :param secret_key: R2 Secret Access Key
    """

    # Cloudflare R2 的 Endpoint URL 格式
    endpoint_url = f"https://{account_id}.r2.cloudflarestorage.com"

    # 建立 S3 客戶端連線
    s3_client = boto3.client(
        service_name="s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",  # R2 填 auto 即可
    )

    try:
        # 執行上傳
        s3_client.upload_file(local_file_path, bucket_name, object_name)
        print(f"✅ 上傳成功: {object_name}")
        return True
    except FileNotFoundError:
        print("❌ 錯誤: 找不到本地檔案")
    except NoCredentialsError:
        print("❌ 錯誤: 憑證無效")
    except ClientError as e:
        print(f"❌ 發生錯誤: {e}")

    return False
