"""Maintenance views — Phase 2 placeholder."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class MaintenancePlaceholderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"detail": "Maintenance module — coming in Phase 2."})
