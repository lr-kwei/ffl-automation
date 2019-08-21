PUBS = [
	{:name => "Twitter", :aud => 156426, :logo => "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQMK4p7YJ2ABCissS-vYpzZXTKlnyyH6VqeLRe0T4gpxIrSNEuonNUeG3w"},
	{:name => "MSN", :aud => 162186, :logo => "http://ncmedia.azureedge.net/ncmedia/2015/01/MSN_Blue_RGB1.png"},
	{:name => "NinthDecimal", :aud => 156466, :logo => "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQY-VBIEnCxvcVWQqkXubKrbCngeJmPI_8huviUFIFA4IH7Hu0"},
	{:name => "4INFO", :aud => 156456, :logo => "http://ww1.prweb.com/prfiles/2014/09/29/12406924/4INFO%20Logo.jpg"},
	{:name => "eBay", :aud => 156476, :logo => "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQYcpQ2_Be_TX8RUNtlZBkAd82Y5jOhSdQABqMf_S_pJ-dH73dIo-Xwursw"},
	{:name => "Yahoo", :aud => 156446, :logo => "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ad/Yahoo_Logo.svg/2000px-Yahoo_Logo.svg.png"},
	{:name => "AOL", :aud => 156436, :logo => "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b6/AOL_logo.svg/2000px-AOL_logo.svg.png"},
	{:name => "Facebook", :aud => 156416, :logo => "http://www.freeiconspng.com/uploads/facebook-announces-clickable-hashtags--resolution-media-17.png"}
]

def get_dms_segments(aud)
	aud.lrc_field_definitions.select{|lrcf| lrcf.enabled}.
		reject{|lrcf| OMITTED_LRCF_ID.include? lrcf.id}.
		map(&:dms_segments).flatten.
		select{|dms_seg| dms_seg.enabled};
end

def get_das_on_segment(seg)
	seg.lrc_field_definition.ada_fields.select{|ada_field| ada_field.status == ADA_FIELD_ACTIVE}.
		map(&:audience_destination_account).select{|ada| ada.status == ADA_ACTIVE}.
		map(&:destination_account).select{|da| da.status == DA_ACTIVE} || []
end

ADA_FIELD_ACTIVE = AdaField.statuses.active
ADA_ACTIVE = AudienceDestinationAccount.statuses.active
DA_ACTIVE = DestinationAccount.statuses.active
OMITTED_LRCF_ID = [
    19417166 # Package U4563215 - strange FB one that was sent through the API but we didn't get a distribution email
	]

aud = LiverampCustomerAccount.where(:id => 156416).
		includes(:lrc_field_definitions => [:dms_segments,
			:ada_fields => [:ada_field_values , :audience_destination_account =>
					[:destination_account =>
						[:server_side_accounts =>
							[:ssa_refresh_requests, :data_sync_jobs]]]]]).
		includes(:lrc_field_definitions => [:lir_fields =>
			[:liveramp_import_request => :liveramp_import_request_events]]).first
		#where("lrc_field_definitions.enabled" => true,
		#	"dms_segments.enabled" => true,
		#	"ada_fields.status" => ADA_FIELD_ACTIVE,
		#	"audience_destination_accounts.status" => ADA_ACTIVE,
		#	"destination_accounts.status" => DA_ACTIVE,
		#	"server_side_accounts.status" => SSA_ACTIVE).first
###

segs = get_dms_segments(aud)

das = []

segs.each do |seg|
  #seg = segs.first
  #get DAs for this segment
  das << get_das_on_segment(seg)
end

das = das.flatten

old_das = []

for da in das
	if ((Time.zone.now - da.created_at).to_i / 1.day) > 60
		old_das << da
	end
end

idlist = old_das.map(&:id,&:name)


delete columns c,e,g-h,k-p
custlist = []
audlist = []
for cust in custlist
   audlist << LiverampCustomerAccount.where(:customer_id => cust, :enabled => true)
end
audlist = audlist.flatten
