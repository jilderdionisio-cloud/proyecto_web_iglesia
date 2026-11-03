from rest_framework import serializers
from .models import Donation

class DonationSerializer(serializers.ModelSerializer):
    display_donor = serializers.SerializerMethodField()
    class Meta:
        model = Donation
        fields = ('id','received_at','amount','concept','method','donor_name','display_donor','is_anonymous','created_at')
        read_only_fields = ('id','display_donor','created_at')
    def get_display_donor(self, obj):
        return 'Anónimo' if obj.is_anonymous else (obj.donor_name or 'Sin nombre')
    def validate(self, attrs):
        if attrs.get('is_anonymous'):
            attrs['donor_name'] = ''
        return attrs
