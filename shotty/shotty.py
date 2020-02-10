import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

@click.group()
def instances():
	"""Command for instances"""

@instances.command ('list')
@click.option('--project', default=None, help="Only instances for this project (tag Project:<name>)")

def list_instances(project):
	"List EC2 instances"
	instances = get_instances(project)


#	if project:
#		filters = [{'Name':'tag:Project', 'Values':["Valkyrie"]}]
#		instances = ec2.instances.filter(Filters=filters)
#	else:
#		instances = ec2.instances.all()


	for i in instances:
		tags = { t['Key']: t['Value'] for t in i.tags or [] }

		print (', '.join ((
			i.id,
			i.instance_type,
			i.placement['AvailabilityZone'],
			i.state['Name'],
			i.public_dns_name,
			tags.get('Project', '<no project>'))))

	return

@instances.command('start')
@click.option('--project', default=None, help='Only instances for project')

def start_instances(project):
	"start EC2 instances"

	instances = get_instances(project)

	for i in instances:
		print ("starting {0}...".format(i.id))
		i.start()

	return

def get_instances (project):
	instances = []

	if project:
		filters = [{'Name':'tag:Project', 'Values':["Valkyrie"]}]
		instances = ec2.instances.filter(Filters=filters)
	else:
		instances = ec2.instances.all()

	return instances

if __name__ == '__main__':
	instances()