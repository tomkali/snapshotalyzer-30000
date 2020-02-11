import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

@click.group()
def cli():
	"""Shotty manages snapshots"""

@cli.group('snapshots')
def snapshots():
	"""Commands for snapshots"""

@snapshots.command ('list')
@click.option('--project', default=None, help="Only snapshots for this project (tag Project:<name>)")

def list_snapshots(project):
	"List EC2 snapshots"
	instances = filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			for s in v.snapshots.all():
				print (", ".join((
				s.id,
				v.id,
				i.id,
				s.state,
				s.progress,
				s.start_time.strftime("%c")
				)))

	return			

@cli.group('volumes')
def volumes():
	"""Commands for volumes"""

@volumes.command ('list')
@click.option('--project', default=None, help="Only instances for this project (tag Project:<name>)")

def list_volumes(project):
	"List EC2 volumes"
	instances = filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			print (", ".join((
			v.id,
			i.id,
			v.state,
			str(v.size) + "GiB",
			v.encrypted and "Encrypted" or "Not Encrypted"
			)))

	return

@cli.group('instances')
def instances():
	"""Command for instances"""

@instances.command('snapshot',
	help="Create snapshots of all volumes")
@click.option('--project', default=None, help="Only instances for this project (tag Project:<name>)")
def create_snapshots(project):
	"Create snapshots of all volumes"
	instances = filter_instances(project)

	for i in instances:
		for v in i.volumes.all():
			print("Creating snapshot of volume {0}".format(v.id))	
			v.create_snapshot(Description="Created by SnapshotAlyzer 30000")

	return


@instances.command ('list')
@click.option('--project', default=None, help="Only instances for this project (tag Project:<name>)")

def list_instances(project):
	"List EC2 instances"
	instances = filter_instances(project)

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

	instances = filter_instances(project)

	for i in instances:
		print ("starting {0}...".format(i.id))
		i.start()

	return

@instances.command('stop')
@click.option('--project', default=None, help='Only instances for project')

def stop_instances(project):
	"start EC2 instances"

	instances = filter_instances(project)

	for i in instances:
		print ("stopping {0}...".format(i.id))
		i.stop()

	return

def filter_instances (project):
	instances = []

	if project:
		filters = [{'Name':'tag:Project', 'Values':["Valkyrie"]}]
		instances = ec2.instances.filter(Filters=filters)
	else:
		instances = ec2.instances.all()

	return instances

if __name__ == '__main__':
	cli()