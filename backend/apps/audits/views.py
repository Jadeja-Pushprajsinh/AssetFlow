"""Audits views — Phase 3 placeholder."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class AuditsPlaceholderView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"detail": "Audit cycles module — coming in Phase 3."})
