##############################################
# $Id: myUtilsTemplate.pm 21509 2020-03-25 11:20:51Z rudolfkoenig $
#
# Save this file as 99_myUtils.pm, and create your own functions in the new
# file. They are then available in every Perl expression.

package main;

use strict;
use warnings;

sub
myUtils_Initialize($$)
{
  my ($hash) = @_;
}

# Enter you functions below _this_ line.

sub createReadings_ESS_Minutenwerte($)
{
my $SELF = shift;
my @readingnames =qw(Timestamp SoC_in_Pct Grid_to_Household_in_W Battery_to_Household_in_W PV_to_Household_in_W PV_to_Battery_in_W PV_to_Grid_in_W PV_power_provision_in_W Household_demand_in_W PVpeak_in_W Load_resistor_in_W Neg_Inverter_AC_power_in_W Pos_Inverter_AC_power_in_W Neg_Inverter_DC_power_in_W Pos_Inverter_DC_power_in_W PFCR_as_measured_in_W PFCRpos_scheduled_in_W PFCRneg_scheduled_in_W Traded_power_in_W PGRD_as_measured_in_W PFRR_as_measured_in_W PFRRpos_reserved_in_W PFRRneg_reserved_in_W PFCRpos_overfulfillment_setpoint_in_W PFCRneg_overfulfillment_setpoint_in_W Control_Power_to_Battery_in_W Battery_to_Control_Power_in_W Deadband_recharge_in_W Recharge_by_power_purchase_in_W Discharge_by_power_sale_in_W ESS_counter_level_discharge_in_Wh HH_counter_level_discharge_in_Wh HH_counter_level_charge_in_Wh PV_counter_level_discharge_in_Wh ESS_counter_level_charge_in_Wh PV_counter_level_charge_in_Wh PVplusHH_counter_level_discharge_in_Wh PVplusHH_counter_level_charge_in_Wh PBH_counter_level_in_Wh PPB_counter_level_in_Wh PRE_counter_level_in_Wh PDI_counter_level_in_Wh PFCRpos_counter_level_in_Wh PFCRneg_counter_level_in_Wh HHpa_in_Wh PFRRpos_counter_level_in_Wh PFRRneg_counter_level_in_Wh Average_Load_Caterva);
my $timestamp = substr(TimeNow(),0,7);
my $filename = "/opt/fhem/log/$SELF-$timestamp.log";
my $last_line = `tail -1 $filename`;
my @readings = split / \d+: /, $last_line;
my $x=0;

foreach (@readings)
 {
 	my $y = sprintf("%02d",$x);
 	my $readingname = $y."_Reading_$y";
 	$readingname = $y."_".$readingnames[$x] if defined $readingnames[$x];
 	fhem("setreading $SELF $readingname $_");
 $x++;
 }
}


1;
