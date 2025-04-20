output "ecr_repository_url" {
  value = aws_ecr_repository.app_repo.repository_url
}

output "instance_public_ip" {
  value = aws_instance.django_host.public_ip
}
