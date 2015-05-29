# Access Control

You can restrict your `@respond_to` and `@hear` to one or more set of groups, using Access Control List or ACL in short. This is very similar to the `admin_only=True` parameter, but you can use different access levels, not only one.

## Usage

To use ACL, you need to specify ACL groups first in your config. An ACL group has to start with `ACL_` and then add the group name with capital letters.


For example let's define the **infra_ops** and the **infra_admins** ACL groups in `config.py`.

```python
# Ops team
ACL_INFRA_OPS = [
    "steven",
    "levi",
]
# Admin team
ACL_INFRA_ADMINS = [
    "wooh",
]
```

You just need to pass the `acl` argument to your `@hear` or `@respond_to` function. The `acl` argument accepts comma separated values in curly braces, example: `acl={"team1", "team2"}`.

Example:

To allow the **infra_ops** and **infra_admins** groups for example to stop EC2 instances, but only allow the **infra_admins** group to terminate the instances.

```python
@respond_to("ec2 instance stop (?P<instance_id>.*)", acl={"infra_ops", "infra_admins"})
def stop_ec2_instance(self, message, instance_id):
    # do AWS stuff

@respond_to("ec2 instance terminate (?P<instance_id>.*)", acl={"infra_admins"})
def terminate_ec2_instance(self, message, instance_id):
    # do AWS stuff
```

So simple as that.