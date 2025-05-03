<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
        Schema::create('moderation_logs', function (Blueprint $table) {
            $table->id();
            $table->string('content_type');
            $table->unsignedBigInteger('content_id');
            $table->string('action_type');
            $table->unsignedBigInteger('moderator_id');
            $table->text('after_state')->nullable();
            $table->enum('severity', ['none', 'low', 'medium', 'high'])->default('none');
            $table->text('reason')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
        Schema::dropIfExists('moderation_logs');
    }
};
