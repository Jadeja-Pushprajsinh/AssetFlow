from rest_framework import serializers
from django.utils import timezone
from .models import Booking


class BookingSerializer(serializers.ModelSerializer):
    asset_tag = serializers.CharField(source='asset.asset_tag', read_only=True)
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    booked_by_name = serializers.CharField(source='booked_by.full_name', read_only=True, default=None)
    computed_status = serializers.CharField(read_only=True)

    class Meta:
        model = Booking
        fields = (
            'id', 'asset', 'asset_tag', 'asset_name',
            'booked_by', 'booked_by_name',
            'start_time', 'end_time',
            'status', 'computed_status', 'purpose',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'status', 'booked_by', 'created_at', 'updated_at')

    def validate(self, data):
        asset = data.get('asset') or (self.instance.asset if self.instance else None)
        start = data.get('start_time') or (self.instance.start_time if self.instance else None)
        end = data.get('end_time') or (self.instance.end_time if self.instance else None)

        if start and end and end <= start:
            raise serializers.ValidationError("end_time must be after start_time.")

        if start and start < timezone.now():
            raise serializers.ValidationError("Bookings cannot start in the past.")

        if asset and not asset.is_bookable:
            raise serializers.ValidationError("This asset is not available for booking.")

        # Overlap check: existing.start < new.end AND existing.end > new.start
        if asset and start and end:
            overlap_qs = Booking.objects.filter(
                asset=asset,
                status__in=['upcoming', 'ongoing'],
                start_time__lt=end,
                end_time__gt=start,
            )
            if self.instance:
                overlap_qs = overlap_qs.exclude(pk=self.instance.pk)
            if overlap_qs.exists():
                raise serializers.ValidationError(
                    "This asset is already booked for the requested time slot."
                )

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request.user, 'employee'):
            validated_data['booked_by'] = request.user.employee
        return super().create(validated_data)
