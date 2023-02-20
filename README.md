### Remove AWS Default VPCs

This Project attempts to delete the AWS default VPC in each region.

**Requirements:**

* docker
* docker-compose
* Valid AWS key



## Setup:

#### Environment Variables

```
AWS_ROLE=
AWS_ACCOUNT_ID=

```
#### Credentials file
Set AWS auth environment variables in the file
```
.env/.env.auth
```

**Usage:**


```bash
# list all vpcs that will be deleted
$ make list-vpcs


# delete all defaults vpcs (This action needs confirmation check terminal)
$ make delete-vpcs
#
```



**Output:**

```
REGION:us-west-1
VPC Id:vpc-077afe19c99727b00
rtb-0af8d17ff020c33c6 is the main route table, continue...
Removing sub-id:  subnet-0500a72ea9f2a320d
acl-0c74f04df9767271c is the default NACL, continue...
Removing sub-id:  subnet-03989cb334e9bbc60
Removing sub-id:  subnet-00bb3cca6bd4e021a
sg-09408dd0c80753eb7 is the default security group, continue...
Removing vpc-id:  vpc-08ecc532f4a95eb36
Detaching and Removing igw-id:  igw-00568594a68f32052
Removing sub-id:  subnet-053b892606c18bbdf
Removing sub-id:  subnet-0abf36bb5cf883867
Removing sub-id:  subnet-056562fafe7390248
Removing sub-id:  subnet-0164927902f6d28cd
rtb-0674c4996fd19541a is the main route table, continue...
Removing sub-id:  subnet-0a0e8cad9c3ebdd37
rtb-0c5d686f1bfc1bbfb is the main route table, continue...
acl-03d0159fa30d14b7a is the default NACL, continue...
acl-03762bbab46a895c2 is the default NACL, continue...
sg-022dce9be83dcb112 is the default security group, continue...
Removing vpc-id:  vpc-0d99f70a1316b743a
sg-08fe76c42aab483d9 is the default security group, continue...
Removing vpc-id:  vpc-0b600a12281131e0f
rtb-0242a5a41ab3cf132 is the main route table, continue...
acl-0b835b5a208389f36 is the default NACL, continue...
sg-046a9b8b0e764427a is the default security group, continue...
Removing vpc-id:  vpc-077afe19c99727b00
All commands finished
```

**References:**

* https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html

