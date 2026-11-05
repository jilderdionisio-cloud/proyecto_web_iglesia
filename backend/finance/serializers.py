from rest_framework import serializers

from .models import Donation


class DonationSerializer(serializers.ModelSerializer):
    donor = serializers.CharField(read_only=True)
    type_label = serializers.CharField(source='get_donation_type_display', read_only=True)
    method_label = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = Donation
        fields = ('id', 'amount', 'donation_type', 'type_label', 'payment_method', 'method_label', 'date', 'is_anonymous', 'member', 'donor_name', 'donor', 'notes', 'created_at', 'updated_at')
        read_only_fields = ('id', 'donor', 'type_label', 'method_label', 'created_at', 'updated_at')

    def validate(self, attrs):
        is_anonymous = attrs.get('is_anonymous', getattr(self.instance, 'is_anonymous', False))
        if is_anonymous:
            attrs['member'] = None
            attrs['donor_name'] = ''
            return attrs
        member = attrs.get('member', getattr(self.instance, 'member', None))
        donor_name = attrs.get('donor_name', getattr(self.instance, 'donor_name', ''))
        if not member and not donor_name.strip():
            raise serializers.ValidationError({'member': 'Indica el miembro o el nombre del donante, o márcala como anónima.'})
        return attrs
