from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Booking
from .serializers import BookingSerializer
from accounts.permissions import IsEmployee


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsEmployee]
    filterset_fields = ['asset', 'status', 'booked_by']
    search_fields = ['asset__asset_tag', 'asset__name', 'purpose']
    ordering_fields = ['start_time', 'end_time', 'created_at']
    ordering = ['start_time']

    def get_queryset(self):
        qs = Booking.objects.select_related('asset', 'booked_by__user').all()
        user = self.request.user
        if not hasattr(user, 'employee'):
            return qs.none()
        emp = user.employee
        if emp.role in ('admin', 'asset_manager'):
            return qs
        return qs.filter(booked_by=emp)

    @action(detail=True, methods=['patch'], url_path='cancel')
    def cancel(self, request, pk=None):
        """PATCH /api/bookings/<pk>/cancel/"""
        booking = self.get_object()
        if booking.status not in ('upcoming', 'ongoing'):
            return Response(
                {'detail': 'Only upcoming or ongoing bookings can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        booking.status = 'cancelled'
        booking.save(update_fields=['status', 'updated_at'])
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=['patch'], url_path='reschedule')
    def reschedule(self, request, pk=None):
        """PATCH /api/bookings/<pk>/reschedule/"""
        booking = self.get_object()
        if booking.status == 'cancelled':
            return Response(
                {'detail': 'Cancelled bookings cannot be rescheduled.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = BookingSerializer(
            booking,
            data=request.data,
            partial=True,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        booking.refresh_from_db()
        booking.status = 'upcoming'
        booking.save(update_fields=['status', 'updated_at'])
        return Response(BookingSerializer(booking).data)

    @action(detail=False, methods=['get'], url_path='calendar')
    def calendar(self, request):
        """GET /api/bookings/calendar/?asset=<id>&from=<date>&to=<date>"""
        asset_id = request.query_params.get('asset')
        from_date = request.query_params.get('from')
        to_date = request.query_params.get('to')
        qs = self.get_queryset().exclude(status='cancelled')
        if asset_id:
            qs = qs.filter(asset_id=asset_id)
        if from_date:
            qs = qs.filter(end_time__date__gte=from_date)
        if to_date:
            qs = qs.filter(start_time__date__lte=to_date)
        serializer = BookingSerializer(qs, many=True)
        return Response(serializer.data)
