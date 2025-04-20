output "instance_public_ip" {
  value = aws_instance.django_host.public_ip
}
